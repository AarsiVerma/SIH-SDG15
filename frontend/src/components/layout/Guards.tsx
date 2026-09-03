"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, clearUserCache } from "@/lib/auth";
import { UserRole } from "@/types/api";

interface AuthGuardProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export default function AuthGuard({ children, allowedRoles }: AuthGuardProps) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const user = await getCurrentUser();
        if (!user) {
          router.push("/login");
          return;
        }
        if (allowedRoles && !allowedRoles.includes(user.role)) {
          router.push("/command"); // or 403 page
          return;
        }
        setAuthorized(true);
      } catch {
        clearUserCache();
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, [router, allowedRoles]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-forest-900">
        <div className="text-gray-400">Verifying access…</div>
      </div>
    );
  }

  if (!authorized) return null;

  return <>{children}</>;
}