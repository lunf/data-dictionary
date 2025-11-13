import { useEffect, useState } from "react";
import { fetchBusinessGlossary, type BusinessTerm } from "../api";


export default function GlossaryList() {
  const [terms, setTerms] = useState<BusinessTerm[]>([]);
  const [loading, setLoading] = useState(true);
  
    useEffect(() => {
      fetchBusinessGlossary()
        .then(setTerms)
        .catch(console.error)
        .finally(() => setLoading(false));
    }, []);

  if (loading) return <p className="text-gray-500">Loading glossary...</p>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-3 text-blue-600">Business Glossary</h2>
      <div className="space-y-3">
        {terms.map((t) => (
          <div
            key={t.id}
            className="p-4 border border-gray-200 bg-white shadow-sm rounded-xl hover:shadow-md"
          >
            <h3 className="font-semibold text-lg text-gray-800">{t.term}</h3>
            <p className="text-gray-700 mt-1">{t.term_definition}</p>
            <div className="mt-2 text-sm text-gray-600">
              <strong>Domain:</strong> {t.business_domain || "N/A"} <br />
              <strong>Context:</strong> {t.term_context}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
