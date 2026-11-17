"use client";

import { useMemo, useState, type FormEvent } from "react";
import { Plus, Search, Trash2, UploadCloud, Info } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Field } from "@/components/ui/field";
import { Input } from "@/components/ui/input";

export type CatalogKind = "coupons" | "campaigns" | "partnerships";

interface CatalogItem {
  id: string;
  name: string;
  detail: string;
  status: "Ativo" | "Agendado" | "Pausado";
  attachment?: string;
}

const CONFIG: Record<CatalogKind, { title: string; description: string; singular: string; nameLabel: string; detailLabel: string; detailPlaceholder: string; hasUpload: boolean; empty: string }> = {
  coupons: {
    title: "Cupons",
    description: "Cadastre e organize os cupons que serão disponibilizados pela plataforma. A conexão com o serviço do módulo responsável será feita na integração.",
    singular: "cupom",
    nameLabel: "Nome do cupom",
    detailLabel: "Código ou benefício",
    detailPlaceholder: "Ex.: BEMVINDO10 — 10% de desconto",
    hasUpload: true,
    empty: "Nenhum cupom cadastrado nesta prévia.",
  },
  campaigns: {
    title: "Campanhas",
    description: "Organize ações de divulgação, período de execução e situação de cada campanha.",
    singular: "campanha",
    nameLabel: "Nome da campanha",
    detailLabel: "Período ou canal",
    detailPlaceholder: "Ex.: Novembro — redes sociais",
    hasUpload: false,
    empty: "Nenhuma campanha cadastrada nesta prévia.",
  },
  partnerships: {
    title: "Parcerias",
    description: "Registre organizações parceiras e os contatos para acompanhamento administrativo.",
    singular: "parceria",
    nameLabel: "Nome da parceria ou organização",
    detailLabel: "Contato ou observação",
    detailPlaceholder: "Ex.: contato@empresa.com",
    hasUpload: false,
    empty: "Nenhuma parceria cadastrada nesta prévia.",
  },
};

/** CRUD local demonstrativo: oferece a experiência visual sem fingir persistência no backend. */
export function AdminCatalogPanel({ kind }: { kind: CatalogKind }) {
  const config = CONFIG[kind];
  const [items, setItems] = useState<CatalogItem[]>([]);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [detail, setDetail] = useState("");
  const [status, setStatus] = useState<CatalogItem["status"]>("Ativo");
  const [attachment, setAttachment] = useState("");
  const [savedMessage, setSavedMessage] = useState("");

  const filtered = useMemo(() => {
    const term = search.trim().toLocaleLowerCase("pt-BR");
    if (!term) return items;
    return items.filter((item) => `${item.name} ${item.detail} ${item.status}`.toLocaleLowerCase("pt-BR").includes(term));
  }, [items, search]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!name.trim() || !detail.trim()) return;
    setItems((current) => [
      { id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`, name: name.trim(), detail: detail.trim(), status, attachment: attachment || undefined },
      ...current,
    ]);
    setName("");
    setDetail("");
    setStatus("Ativo");
    setAttachment("");
    setShowForm(false);
    setSavedMessage(`Prévia de ${config.singular} adicionada nesta sessão.`);
  }

  return (
    <section>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="mb-1 text-xs font-bold uppercase tracking-[0.18em] text-brand-green">Administração</p>
          <h1 className="font-display text-3xl font-bold text-brand-blue">{config.title}</h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-500">{config.description}</p>
        </div>
        <Button onClick={() => { setShowForm((value) => !value); setSavedMessage(""); }}>
          <Plus className="mr-2 h-4 w-4" aria-hidden /> {showForm ? "Fechar formulário" : `Novo ${config.singular}`}
        </Button>
      </div>

      <div className="mb-5 flex items-start gap-3 rounded-xl border border-brand-amber/35 bg-brand-amber-soft/50 p-4 text-sm text-slate-700">
        <Info className="mt-0.5 h-5 w-5 shrink-0 text-brand-amber" aria-hidden />
        <p><strong>Prévia de frontend:</strong> os registros são mantidos somente no estado desta página e desaparecem ao atualizar. A persistência e a integração com as APIs serão implementadas depois, junto com o backend e o banco compartilhado.</p>
      </div>

      {savedMessage ? <p role="status" className="mb-4 rounded-lg bg-brand-green-soft px-4 py-3 text-sm text-brand-green">{savedMessage}</p> : null}

      {showForm ? (
        <form onSubmit={handleSubmit} className="mb-6 rounded-2xl border border-brand-blue-soft bg-white p-5 shadow-sm">
          <h2 className="mb-4 font-display text-xl font-bold text-brand-blue">Cadastrar {config.singular}</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <Field label={config.nameLabel}>
              <Input value={name} onChange={(event) => setName(event.target.value)} required placeholder="Digite um nome" />
            </Field>
            <Field label={config.detailLabel}>
              <Input value={detail} onChange={(event) => setDetail(event.target.value)} required placeholder={config.detailPlaceholder} />
            </Field>
            <Field label="Situação">
              <select value={status} onChange={(event) => setStatus(event.target.value as CatalogItem["status"])} className="admin-input">
                <option>Ativo</option>
                <option>Agendado</option>
                <option>Pausado</option>
              </select>
            </Field>
            {config.hasUpload ? (
              <Field label="Imagem ou material do cupom (opcional)">
                <label className="flex min-h-10 cursor-pointer items-center gap-2 rounded-lg border border-dashed border-brand-blue/40 bg-brand-blue-soft/20 px-3 py-2 text-sm text-slate-600 transition hover:border-brand-blue hover:bg-brand-blue-soft/40">
                  <UploadCloud className="h-4 w-4 text-brand-blue" aria-hidden />
                  <span className="truncate">{attachment || "Selecionar arquivo"}</span>
                  <input type="file" accept="image/*,.pdf" className="sr-only" onChange={(event) => setAttachment(event.target.files?.[0]?.name ?? "")} />
                </label>
              </Field>
            ) : null}
          </div>
          <div className="mt-5 flex flex-wrap justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancelar</Button>
            <Button type="submit" variant="red">Adicionar à prévia</Button>
          </div>
        </form>
      ) : null}

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-display text-xl font-bold text-brand-blue">Registros</h2>
        <label className="relative block w-full sm:max-w-xs">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden />
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder={`Buscar ${config.title.toLocaleLowerCase("pt-BR")}`} className="admin-input pl-9" />
        </label>
      </div>

      {filtered.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-brand-blue-soft bg-white px-5 py-12 text-center">
          <p className="font-semibold text-brand-blue">{search ? "Nenhum resultado encontrado." : config.empty}</p>
          <p className="mt-2 text-sm text-slate-500">Use “Novo {config.singular}” para testar o formulário da interface.</p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-2xl border border-brand-blue-soft bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[38rem] text-left text-sm">
              <thead className="bg-brand-blue-soft/35 text-xs uppercase tracking-wide text-slate-500">
                <tr><th className="px-4 py-3">Nome</th><th className="px-4 py-3">Detalhes</th><th className="px-4 py-3">Situação</th><th className="px-4 py-3">Material</th><th className="px-4 py-3"><span className="sr-only">Ações</span></th></tr>
              </thead>
              <tbody className="divide-y divide-brand-blue-soft/70">
                {filtered.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-3 font-semibold text-ink">{item.name}</td>
                    <td className="px-4 py-3 text-slate-600">{item.detail}</td>
                    <td className="px-4 py-3"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${item.status === "Pausado" ? "bg-slate-100 text-slate-600" : item.status === "Agendado" ? "bg-brand-amber-soft text-amber-800" : "bg-brand-green-soft text-brand-green"}`}>{item.status}</span></td>
                    <td className="max-w-40 truncate px-4 py-3 text-xs text-slate-500">{item.attachment ?? "—"}</td>
                    <td className="px-4 py-3 text-right"><button type="button" aria-label={`Remover ${item.name}`} onClick={() => setItems((current) => current.filter((entry) => entry.id !== item.id))} className="rounded-lg p-2 text-slate-400 transition hover:bg-brand-red/10 hover:text-brand-red"><Trash2 className="h-4 w-4" aria-hidden /></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
