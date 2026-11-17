"use client";

import { ChevronDown, Home, LogOut, UserCircle, LayoutDashboard } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useLogout } from "@/features/auth/hooks";
import type { User } from "@/features/auth/types";

/** Menu de conta; administradores vão diretamente para a administração do D01. */
export function UserMenu({ user }: { user: User }) {
  const router = useRouter();
  const logout = useLogout();
  const isAdmin = user.role === "admin";

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        aria-label={`Menu da conta de ${user.full_name}`}
        className="flex items-center gap-1 rounded-full p-1 text-brand-blue transition hover:bg-brand-blue-soft/60 focus-visible:ring-2 focus-visible:ring-brand-blue"
      >
        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-blue-soft/60">
          <UserCircle className="h-7 w-7" aria-hidden />
        </span>
        <ChevronDown className="h-4 w-4" aria-hidden />
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <p className="max-w-56 truncate px-3 py-2 text-xs text-slate-500">{user.full_name}</p>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/">
            <Home className="h-4 w-4" aria-hidden /> Página Inicial
          </Link>
        </DropdownMenuItem>
        {isAdmin ? (
          <DropdownMenuItem asChild>
            <Link href="/admin">
              <LayoutDashboard className="h-4 w-4" aria-hidden /> Meu Dashboard
            </Link>
          </DropdownMenuItem>
        ) : (
          <DropdownMenuItem asChild>
            <Link href="/painel">
              <LayoutDashboard className="h-4 w-4" aria-hidden /> Meu Dashboard
            </Link>
          </DropdownMenuItem>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onSelect={() => logout.mutate(undefined, { onSettled: () => router.push("/") })}
          disabled={logout.isPending}
        >
          <LogOut className="h-4 w-4" aria-hidden /> {logout.isPending ? "Saindo..." : "Log Out"}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
