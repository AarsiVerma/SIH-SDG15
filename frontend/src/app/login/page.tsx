"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api/client";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("/auth/login", { email, password });
      router.push("/command");
    } catch (e: any) {
      setError(e.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex h-screen w-full items-center justify-center bg-forest-900 p-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">VANRAKSHA AI</h1>
          <p className="text-gray-400 mt-2">Sign in to Command Centre</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 bg-forest-800 rounded-xl border border-forest-700 p-6">
          {error && (
            <div className="bg-red-900/30 border border-red-700 text-red-300 p-3 rounded text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm text-gray-300 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-forest-900 border border-forest-700 rounded px-3 py-2 text-gray-100 focus:outline-none focus:ring-2 focus:ring-forest-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm text-gray-300 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-forest-900 border border-forest-700 rounded px-3 py-2 text-gray-100 focus:outline-none focus:ring-2 focus:ring-forest-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-forest-600 hover:bg-forest-500 text-white py-2 rounded disabled:opacity-50 transition"
          >
            {loading ? "Signing in…" : "Sign In"}
          </button>
        </form>

        <div className="mt-4 text-center text-sm text-gray-500">
          Demo: admin@vanraksha.local / changeme
        </div>
      </div>
    </main>
  );
}