/**
 * ============================================================================
 * FlowForge - AI Chat Widget
 * ============================================================================
 * 
 * WHY THIS FILE EXISTS
 * --------------------
 * This file creates the React Component for our AI Chatbot. 
 * A "Component" is like a reusable Lego block for building user interfaces.
 * 
 * This specific block creates the floating "Sparkle" button in the bottom 
 * right corner of the screen, and the chat window that pops up when you click it.
 * 
 * We use 'Tailwind CSS' (the long text in className="...") to make it look 
 * stunning with a modern "Glassmorphism" (frosted glass) design.
 */

// =====================================================
// Imports
// =====================================================

// We import React features (Hooks). 
// - useState: Helps the component "remember" things (like if the chat is open).
// - useEffect: Helps us run code automatically (like auto-scrolling).
// - useRef: Helps us directly control a specific piece of the screen (like telling the chat to scroll).
import React, { useState, useEffect, useRef } from 'react';

// We import icons from the 'lucide-react' library to make the UI look good.
import { MessageSquare, X, Send, Sparkles, Loader2, Trash2 } from 'lucide-react';

// We import ReactMarkdown to easily display bold text and lists from the AI.
import ReactMarkdown from 'react-markdown';


// =====================================================
// The Main Component
// =====================================================

// We define our component function. We export it so App.jsx can use it.
export default function AiChatbot({ boardId = null }) {
    
    // -------------------------------------------------
    // State Variables (The component's memory)
    // -------------------------------------------------
    
    // 'isOpen' remembers if the chat window is visible (true) or hidden (false).
    // 'setIsOpen' is the function we call to change that memory.
    const [isOpen, setIsOpen] = useState(false);
    
    // 'messages' remembers the history of the conversation. 
    // It starts as an empty array [].
    const [messages, setMessages] = useState([]);
    
    // 'inputValue' remembers what the user is currently typing in the text box.
    const [inputValue, setInputValue] = useState('');
    
    // 'isLoading' remembers if we are currently waiting for the AI to reply.
    const [isLoading, setIsLoading] = useState(false);

    // -------------------------------------------------
    // References (Direct links to the screen)
    // -------------------------------------------------
    
    // We create a 'ref' to point to the bottom of our messages list.
    // We need this so we can automatically scroll down when a new message appears.
    const messagesEndRef = useRef(null);

    // -------------------------------------------------
    // Effects (Automatic Actions)
    // -------------------------------------------------
    
    // 'useEffect' runs a block of code automatically.
    // The '[messages]' at the end means: "Run this code every time 'messages' changes."
    useEffect(() => {
        // If the chat is open, smoothly scroll to the bottom of the messages.
        if (isOpen && messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, isOpen]);


    // -------------------------------------------------
    // Actions (What happens when the user does something)
    // -------------------------------------------------

    // This function runs when the user clicks the "Send" button or presses Enter.
    const handleSendMessage = async (e) => {
        // 'e' is the "Event". 
        // 'e.preventDefault()' stops the browser from doing its default behavior.
        // For example, if this was in a <form>, it stops the page from reloading!
        if (e) e.preventDefault();

        // '.trim()' removes accidental empty spaces at the start/end of the text.
        const trimmedMessage = inputValue.trim();
        
        // If the message is empty, don't do anything. Just stop.
        if (!trimmedMessage) return;

        // 1. Create a new message object representing what the user just said.
        const newUserMsg = { text: trimmedMessage, sender: 'user' };
        
        // 2. Add the new message to our chat history.
        // 'prev => [...prev, newUserMsg]' means: "Take the previous messages, 
        // copy them all, and stick the new one at the end."
        setMessages((prev) => [...prev, newUserMsg]);
        
        // 3. Clear the text box so the user can type their next message.
        setInputValue('');
        
        // 4. Turn on the "Loading" animation.
        setIsLoading(true);

        // 5. Try to talk to our FastAPI backend.
        try {
            // We get the user's secret login token from the browser's Local Storage.
            const token = localStorage.getItem('token');
            
            // We use 'fetch()' to send a network request to our Python server.
            const response = await fetch('http://localhost:8000/api/ai/chat', {
                method: 'POST', // POST means we are sending data TO the server.
                headers: {
                    'Content-Type': 'application/json', // We are sending JSON data.
                    'Authorization': `Bearer ${token}`, // We prove we are logged in using our token.
                },
                // We include board_id so the AI searches the correct project.
                // board_id may be null (e.g., from the Dashboard) — that's fine, the backend
                // will fall back to a cross-project search.
                body: JSON.stringify({
                    user_message: trimmedMessage,
                    board_id: boardId ? parseInt(boardId) : null,
                }),
            });

            // If the server replies with an error code (like 401 Unauthorized)...
            if (!response.ok) {
                // We "throw" an error, which instantly jumps down to the 'catch' block below.
                throw new Error('Failed to communicate with AI');
            }

            // We convert the server's JSON text back into a Javascript object.
            const data = await response.json();
            
            // We create a new message object representing what the AI said.
            const newAiMsg = { 
                text: data.response, 
                sender: 'ai',
                sources: data.sources 
            };
            
            // We add the AI's message to our chat history.
            setMessages((prev) => [...prev, newAiMsg]);

        } catch (error) {
            // If ANYTHING went wrong (no internet, server crashed, bad token)...
            console.error("AI Chat Error:", error);
            
            // We show a red error message in the chat so the user knows what happened.
            setMessages((prev) => [...prev, { 
                text: "Sorry, I couldn't connect to the server right now. Please try again.", 
                sender: 'error' 
            }]);
        } finally {
            // 'finally' runs no matter what happens (success or failure).
            // We turn off the loading animation.
            setIsLoading(false);
        }
    };

    // This lets users click our pre-made suggestion buttons.
    const handleSuggestionClick = (text) => {
        // We put the text in the input box...
        setInputValue(text);
        // ...and we wait a tiny bit (to let React update) and then we pretend the user hit send!
        setTimeout(() => {
            const fakeEvent = { preventDefault: () => {} };
            handleSendMessage(fakeEvent);
        }, 50);
    };


    // =====================================================
    // The User Interface (JSX)
    // =====================================================
    
    return (
        // The outer container. 'fixed bottom-6 right-6' glues it to the bottom-right corner.
        // 'z-50' makes sure it stays on top of everything else on the screen.
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
            
            {/* -------------------------------------------------
                THE CHAT WINDOW (Only shows if isOpen is true)
                ------------------------------------------------- */}
            {isOpen && (
                // This huge list of classes is Tailwind CSS!
                // 'bg-gray-900/90' is dark gray but slightly transparent (/90).
                // 'backdrop-blur-xl' creates the beautiful frosted glass effect.
                // 'rounded-2xl' makes the corners nice and round.
                <div className="mb-4 w-[350px] sm:w-[400px] h-[550px] max-h-[80vh] flex flex-col bg-gray-900/90 backdrop-blur-xl border border-gray-700/50 rounded-2xl shadow-2xl overflow-hidden animate-in slide-in-from-bottom-5 fade-in duration-300">
                    
                    {/* Header Section */}
                    <div className="flex items-center justify-between p-4 bg-gradient-to-r from-indigo-600/80 to-purple-600/80 border-b border-white/10">
                        <div className="flex items-center space-x-2">
                            <Sparkles className="w-5 h-5 text-white" />
                            <h3 className="font-semibold text-white">FlowForge AI</h3>
                        </div>
                        <div className="flex items-center space-x-2">
                            {/* Clear Chat Button */}
                            <button 
                                onClick={() => setMessages([])}
                                className="p-1.5 text-white/70 hover:text-white hover:bg-white/20 rounded-lg transition"
                                title="Clear Chat"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                            {/* Close Chat Button */}
                            <button 
                                onClick={() => setIsOpen(false)}
                                className="p-1.5 text-white/70 hover:text-white hover:bg-white/20 rounded-lg transition"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    {/* Messages Area (Where the chatting happens) */}
                    {/* 'flex-1 overflow-y-auto' makes this area stretch to fill space and scroll if it gets too long. */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        
                        {/* Welcome Message (If the chat is empty) */}
                        {messages.length === 0 && (
                            <div className="flex flex-col items-center justify-center h-full text-center space-y-4 opacity-70">
                                <Sparkles className="w-12 h-12 text-indigo-400 mb-2" />
                                <p className="text-gray-300 text-sm">
                                    I am your intelligent project assistant.<br/>
                                    Ask me about your tasks, priorities, or projects!
                                </p>
                                {/* Quick Suggestion Chips */}
                                <div className="flex flex-wrap gap-2 justify-center mt-4">
                                    <button onClick={() => handleSuggestionClick(boardId ? "Summarize all tasks on this board" : "Summarize my pending tasks")} className="text-xs bg-gray-800 hover:bg-indigo-600/50 text-gray-300 px-3 py-1.5 rounded-full border border-gray-700 transition">
                                        {boardId ? "Summarize board tasks" : "Summarize my tasks"}
                                    </button>
                                    <button onClick={() => handleSuggestionClick("What are my HIGH priority tasks?")} className="text-xs bg-gray-800 hover:bg-indigo-600/50 text-gray-300 px-3 py-1.5 rounded-full border border-gray-700 transition">What's high priority?</button>
                                    {boardId && (
                                        <button onClick={() => handleSuggestionClick("List all tasks that are not done yet")} className="text-xs bg-gray-800 hover:bg-indigo-600/50 text-gray-300 px-3 py-1.5 rounded-full border border-gray-700 transition">What's not done yet?</button>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* We use '.map()' to loop over every message in our history and draw it on the screen. */}
                        {messages.map((msg, idx) => (
                            <div 
                                key={idx} 
                                // We check if the sender is 'user'. If so, we push it to the right (justify-end). If AI, push left (justify-start).
                                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div 
                                    // We color the user's bubble purple, and the AI's bubble dark gray.
                                    className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
                                        msg.sender === 'user' 
                                            ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md' 
                                            : msg.sender === 'error'
                                                ? 'bg-red-500/20 text-red-200 border border-red-500/50'
                                                : 'bg-gray-800/80 text-gray-200 border border-gray-700 shadow-sm'
                                    }`}
                                >
                                    {/* If it's an AI message, we use ReactMarkdown so **bold** text actually looks bold! */}
                                    {msg.sender === 'ai' ? (
                                        <div className="prose prose-invert prose-sm max-w-none">
                                            <ReactMarkdown>{msg.text}</ReactMarkdown>
                                        </div>
                                    ) : (
                                        // If it's a user or error message, just show plain text.
                                        <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                                    )}
                                </div>
                            </div>
                        ))}

                        {/* Loading Indicator (Shows while we wait for Gemini) */}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-gray-800/80 border border-gray-700 rounded-2xl px-4 py-3 flex items-center space-x-2">
                                    {/* 'animate-spin' makes the loading circle turn forever. */}
                                    <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
                                    <span className="text-sm text-gray-400">Thinking...</span>
                                </div>
                            </div>
                        )}
                        
                        {/* This invisible div acts as an "anchor" so we know where the bottom of the list is. */}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area (Where you type) */}
                    <div className="p-3 bg-gray-900 border-t border-gray-800">
                        {/* We use a <form> so the user can press 'Enter' to submit. */}
                        <form onSubmit={handleSendMessage} className="relative flex items-center">
                            <input
                                type="text"
                                value={inputValue}
                                // 'onChange' runs every time the user presses a key, updating our memory.
                                onChange={(e) => setInputValue(e.target.value)}
                                placeholder="Ask about your projects..."
                                className="w-full bg-gray-800 text-gray-200 text-sm rounded-xl pl-4 pr-12 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 border border-gray-700 transition"
                            />
                            {/* The Send Button inside the input box */}
                            <button
                                type="submit"
                                disabled={isLoading || !inputValue.trim()}
                                className="absolute right-2 p-1.5 text-gray-400 hover:text-indigo-400 disabled:opacity-50 disabled:hover:text-gray-400 transition rounded-lg hover:bg-gray-700"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </form>
                    </div>
                </div>
            )}

            {/* -------------------------------------------------
                THE FLOATING BUTTON
                ------------------------------------------------- */}
            <button
                // When clicked, we flip the 'isOpen' memory (true becomes false, false becomes true).
                onClick={() => setIsOpen(!isOpen)}
                // This makes it a big, beautiful purple/indigo circle with a shadow that bounces on hover.
                className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white shadow-[0_0_20px_rgba(99,102,241,0.4)] hover:shadow-[0_0_30px_rgba(99,102,241,0.6)] hover:scale-105 transition-all duration-300"
            >
                {/* If the chat is open, show an X. If closed, show a Sparkle icon. */}
                {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
            </button>
        </div>
    );
}
