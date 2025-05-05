'use client';

import { QuoteDetail } from "@/app/page";

interface CustomerInfo {
  name: string;
  email: string;
  phone: string;
  company?: string;
}

interface QuoteDetailsProps {
  customerInfo: CustomerInfo | null;
  quoteDetails: QuoteDetail[] | null;
}

export default function QuoteDetails({ customerInfo, quoteDetails }: QuoteDetailsProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-4 space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-4">Informações do Cliente</h2>
        {customerInfo?.name ? (
          <div className="space-y-2">
            <p><span className="font-medium">Nome:</span> {customerInfo.name}</p>
            {customerInfo.email && <p><span className="font-medium">Email:</span> {customerInfo.email}</p>}
            {customerInfo.phone && <p><span className="font-medium">Telefone:</span> {customerInfo.phone}</p>}
            {customerInfo.company && (
              <p><span className="font-medium">Empresa:</span> {customerInfo.company}</p>
            )}
          </div>
        ) : (
          <p className="text-gray-500 italic">Nenhuma informação.</p>
        )}
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Dados do Pedido</h2>
        {quoteDetails && quoteDetails.length > 0 ? quoteDetails.map((quoteDetail, index) => (
          <div
            key={quoteDetail.id}
            className="space-y-2"
          >
            <p><span className="font-medium">{index + 1}.</span> {quoteDetail.product_name}</p>

            {Number(quoteDetail.quantity) > 0 && (
              <p><span className="font-medium">Quantidade:</span> {quoteDetail.quantity}</p>
            )}
            
            {quoteDetail.specifications && (
              <div>
                <p className="font-medium mb-1">Especificações:</p>
                <p className="text-sm">{quoteDetail.specifications}</p>
              </div>
            )}
            
            {quoteDetail.additional_notes && (
              <div>
                <p className="font-medium">Observações:</p>
                <p className="text-sm">{quoteDetail.additional_notes}</p>
              </div>
            )}
          </div>
        )) : (
          <p className="text-gray-500 italic">Nenhum item.</p>
        )}
      </div>
    </div>
  );
}
