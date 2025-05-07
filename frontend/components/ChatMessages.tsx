'use client';

import { useEffect, useRef } from 'react';
import { parse_message } from '@/services/text-service';

interface Message {
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  current_step?: string;
  current_product?: {
    name: string;
    description: string;
    price: number;
    category: string;
  };
}

interface ChatMessagesProps {
  messages: Message[];
}

export default function ChatMessages({ messages }: ChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleAddToOrder = (message: Message) => {
    alert('Adicionar ao pedido');

    console.log(message);
  }

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 ">
      <div className="space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="text-md whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: parse_message(message.content) }}></p>

              <p className="text-sm mt-1 opacity-75">
                {new Date(message.timestamp).toLocaleTimeString()}
              </p>

              {(message.current_step === "add_to_order" && message.current_product) && (
                <button onClick={() => handleAddToOrder(message)} className="mt-4 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 cursor-pointer disabled:cursor-not-allowed">
                  Adicionar {message.current_product?.name} ao Pedido
                </button>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
