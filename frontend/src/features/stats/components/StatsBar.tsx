"use client";

import { usePublicStats } from "@/features/stats/hooks";
import { formatStat } from "@/lib/utils";

const DEMO_STATS = [
  { value: "15k", label: "Usuários ativos" },
  { value: "850+", label: "Prestadores" },
  { value: "2.4k", label: "Benefícios" },
  { value: "R$ 1.2M", label: "Economizados" },
];

/** Faixa azul full-bleed; exibe dados da API ou números ilustrativos até a integração. */
export function StatsBar() {
  const { data, isPending, isError } = usePublicStats();
  const hasLiveData = Boolean(data && !isError);
  const items = hasLiveData && data
    ? [
        { value: formatStat(data.active_users), label: "Usuários ativos" },
        { value: formatStat(data.providers), label: "Prestadores" },
        { value: formatStat(data.benefits), label: "Benefícios" },
        { value: `R$ ${formatStat(Math.round(data.savings_cents / 100))}`, label: "Economizados" },
      ]
    : DEMO_STATS;

  return (
    <section aria-label="Números da plataforma" className="w-full bg-brand-blue text-white">
      <dl className="grid w-full grid-cols-2 divide-x divide-y divide-white/15 md:grid-cols-4 md:divide-y-0">
        {isPending && !data
          ? DEMO_STATS.map((item) => (
              <div key={item.label} className="px-4 py-8 text-center sm:py-10" aria-busy="true">
                <div className="mx-auto h-10 w-24 animate-pulse rounded bg-white/15" />
                <dt className="mt-2 text-xs font-semibold uppercase tracking-wider text-white/70">{item.label}</dt>
              </div>
            ))
          : items.map((item) => (
              <div key={item.label} className="px-4 py-8 text-center sm:py-10">
                <dd className="font-brand text-4xl font-bold leading-none text-white sm:text-5xl">{item.value}</dd>
                <dt className="mt-3 text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-white/75 sm:text-xs">
                  {item.label}
                </dt>
              </div>
            ))}
      </dl>
      {!hasLiveData ? (
        <p className="px-4 pb-3 text-center text-[0.65rem] text-white/55">
          Números ilustrativos para visualização do protótipo; métricas reais serão conectadas ao banco compartilhado.
        </p>
      ) : null}
    </section>
  );
}
