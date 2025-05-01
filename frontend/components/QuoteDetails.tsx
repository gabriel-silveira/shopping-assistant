'use client';

interface CustomerInfo {
  name: string;
  email: string;
  phone: string;
  company?: string;
}

interface QuoteDetails {
  product_name: string;
  quantity: number;
  specifications: string;
  additional_notes?: string;
}

interface QuoteDetailsProps {
  customerInfo: CustomerInfo | null;
  quoteDetails: QuoteDetails | null;
}

export default function QuoteDetails({ customerInfo, quoteDetails }: QuoteDetailsProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-4 space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-4">Informações do Cliente</h2>
        {customerInfo ? (
          <div className="space-y-2">
            <p><span className="font-medium">Nome:</span> {customerInfo.name}</p>
            <p><span className="font-medium">Email:</span> {customerInfo.email}</p>
            <p><span className="font-medium">Telefone:</span> {customerInfo.phone}</p>
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
        {quoteDetails ? (
          <div className="space-y-2">
            <p><span className="font-medium">Produto:</span> {quoteDetails.product_name}</p>
            <p><span className="font-medium">Quantidade:</span> {quoteDetails.quantity}</p>
            
            {quoteDetails.specifications && (
              <div>
                <p className="font-medium mb-1">Especificações:</p>
                <p className="text-sm">{quoteDetails.specifications}</p>
              </div>
            )}
            
            {quoteDetails.additional_notes && (
              <div>
                <p className="font-medium">Observações:</p>
                <p className="text-sm">{quoteDetails.additional_notes}</p>
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-500 italic">Nenhum item.</p>
        )}
      </div>
    </div>
  );
}
