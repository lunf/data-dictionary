import { useEffect, useState } from "react";
import { fetchBusinessDomains, type BusinessDomain } from "../api";

export default function DomainList() {
  const [domains, setDomains] = useState<BusinessDomain[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBusinessDomains()
      .then(setDomains)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500">Loading domains...</p>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-3 text-blue-600">Business Domains</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {domains.map((d) => (
          <div
            key={d.id}
            className="p-4 border border-gray-200 bg-white shadow-sm rounded-xl hover:shadow-md"
          >
            <h3 className="text-gray-700 font-semibold text-lg">{d.business_value}</h3>
            <p className="text-sm text-gray-600 mt-1">{d.domain_description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
