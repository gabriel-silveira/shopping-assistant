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
    <div className="container mx-auto h-full p-8">
      <div className="max-w-4xl mx-auto h-full bg-white rounded-xl shadow-xl flex flex-col">
        {/* Cabeçalho da seção */}
        <div className="py-4 px-6 rounded-t-xl" style={{ backgroundColor: '#34303C' }}>
          <h1 className="text-2xl font-semibold text-white">Assistente de Orçamentos</h1>
        </div>

        {/* Container de mensagens com rolagem */}
        <div className="flex-1 overflow-hidden">
          <div className="h-full overflow-y-auto px-6">
            <ChatMessages messages={messages} />
          </div>
        </div>

        {/* Input fixo no rodapé */}
        <div className="p-6 border-t">
          <ChatInput onSendMessage={sendMessage} disabled={!isConnected} />
        </div>
      </div>
    </div>
  );
}
