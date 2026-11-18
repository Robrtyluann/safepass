"use client";

import { ArrowUpRight, LayoutDashboard, ShieldCheck } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";

const DASHBOARD_URL = process.env.NEXT_PUBLIC_D02_DASHBOARD_URL;

/** Página de encaminhamento: o Meu Dashboard é responsabilidade do Desafio 02. */
export function DashboardPlaceholder() {
  return (
    <section className="mx-auto max-w-3xl px-6 py-20 sm:py-28">
      <div className="rounded-3xl border border-brand-blue-soft bg-white p-8 text-center shadow-sm sm:p-12">
        <span className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-blue-soft text-brand-blue">
          <LayoutDashboard className="h-8 w-8" aria-hidden />
        </span>
        <p className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-brand-green">Integração entre squads</p>
        <h1 className="font-display text-3xl font-bold text-brand-blue">Meu Dashboard</h1>
        <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-slate-600">
          A área de Dashboard do usuário está sendo desenvolvida pelo Desafio 02. Esta página é apenas o ponto de integração do Desafio 01 e não duplica as funcionalidades de pontos, cupons, dependentes ou marketplace.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          {DASHBOARD_URL ? (
            <a href={DASHBOARD_URL} className="inline-flex min-h-11 items-center justify-center gap-2 rounded-full bg-brand-blue px-5 py-2 text-sm font-semibold text-white transition hover:bg-brand-blue/90">
              Abrir Meu Dashboard <ArrowUpRight className="h-4 w-4" aria-hidden />
            </a>
          ) : (
            <Button disabled title="Configure NEXT_PUBLIC_D02_DASHBOARD_URL quando o endereço do Desafio 02 estiver definido">
              Dashboard aguardando integração
            </Button>
          )}
          <Link href="/" className="inline-flex min-h-11 items-center justify-center rounded-full border border-brand-blue-soft px-5 py-2 text-sm font-semibold text-brand-blue transition hover:bg-brand-blue-soft/40">
            Voltar à página inicial
          </Link>
        </div>
        <div className="mt-8 flex items-center justify-center gap-2 text-xs text-slate-400">
          <ShieldCheck className="h-4 w-4" aria-hidden /> Sua conta e autenticação são compartilhadas entre os módulos SAFEpass.
        </div>
      </div>
    </section>
  );
}
