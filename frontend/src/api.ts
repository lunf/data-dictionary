export interface BusinessDomain {
  id: number;
  business_value: string;
  domain_description?: string;
}

export interface BusinessTerm {
  id: number;
  term: string;
  term_definition: string;
  business_domain?: string;
  term_context?: string;
}

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error ${response.status}: ${errorText}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchBusinessDomains(): Promise<BusinessDomain[]> {
  const res = await fetch(`${BASE_URL}/api/business-domain`);
  return handleResponse<BusinessDomain[]>(res);
}

export async function fetchBusinessGlossary(): Promise<BusinessTerm[]> {
  const res = await fetch(`${BASE_URL}/api/business-glossary`);
  return handleResponse<BusinessTerm[]>(res);
}
