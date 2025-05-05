'use client';

import { useState, useEffect, useRef } from 'react';
import ChatInput from '@/components/ChatInput';
import ChatMessages from '@/components/ChatMessages';
// import QuoteDetails from '@/components/QuoteDetails';

interface ChatMessage {
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

interface CustomerInfo {
  name: string;
  email: string;
  phone: string;
  company?: string;
}

export interface QuoteDetail {
  id?: string;
  product_name: string;
  quantity: number;
  specifications: string;
  additional_notes?: string;
}

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [customerInfo, setCustomerInfo] = useState<CustomerInfo | null>(null);
  const [quoteDetails, setQuoteDetails] = useState<QuoteDetail[] | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const clientId = Math.random().toString(36).substring(7);
    wsRef.current = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

    wsRef.current.onopen = () => {
      setIsConnected(true);
    };

    wsRef.current.onmessage = (event) => {
      const response = JSON.parse(event.data);
      setMessages(prev => [...prev, response.message]);
      if (response.customer_info) setCustomerInfo(response.customer_info);
      if (response.quote_details) setQuoteDetails(response.quote_details);
    };

    wsRef.current.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const sendMessage = (content: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message: ChatMessage = {
        content,
        role: 'user',
        timestamp: new Date().toISOString(),
      };
      console.log(message);
      wsRef.current.send(JSON.stringify(message));
      setMessages(prev => [...prev, message]);
    }
  };

  return (
    <main className="flex min-h-screen bg-gray-100">
      <div className="flex-1 flex flex-col p-4 overflow-hidden">
        <h1 className="text-2xl font-bold mb-4">Assistente de Orçamentos</h1>
        <div className="flex-1 bg-white rounded-lg shadow-lg overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto">
            <ChatMessages messages={messages} />
          </div>
          <ChatInput onSendMessage={sendMessage} disabled={!isConnected} />
        </div>
      </div>
    </main>
  );
}
