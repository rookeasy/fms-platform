"use client";

import type { FormEvent } from "react";

import { StatusBadge } from "@/components/StatusBadge";
import { buildingContactTypes, formatControlledValue } from "@/lib/controlled-values";
import type { BuildingContact, BuildingContactPayload } from "@/lib/fms-api";

type BuildingContactsPanelProps = {
  contacts: BuildingContact[];
  isSubmitting: boolean;
  onCreate: (payload: BuildingContactPayload) => Promise<void>;
  onDelete: (contactId: string) => Promise<void>;
};

function formValue(form: HTMLFormElement, name: string) {
  return String(new FormData(form).get(name) ?? "").trim();
}

export function BuildingContactsPanel({ contacts, isSubmitting, onCreate, onDelete }: BuildingContactsPanelProps) {
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    await onCreate({
      contact_type: formValue(form, "contact_type"),
      name: formValue(form, "name"),
      company: formValue(form, "company") || null,
      job_title: formValue(form, "job_title") || null,
      email: formValue(form, "email") || null,
      phone: formValue(form, "phone") || null,
      mobile: formValue(form, "mobile") || null,
      is_primary: new FormData(form).get("is_primary") === "on",
      is_emergency_contact: new FormData(form).get("is_emergency_contact") === "on",
      notes: formValue(form, "notes") || null
    });
    form.reset();
  }

  return (
    <section className="space-y-4">
      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-950">Contacts</h2>
        {contacts.length === 0 ? (
          <p className="mt-2 text-sm text-slate-600">No building contacts have been added yet.</p>
        ) : (
          <div className="mt-4 divide-y divide-slate-100">
            {contacts.map((contact) => (
              <div key={contact.id} className="flex flex-wrap items-start justify-between gap-4 py-4">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="font-semibold text-slate-950">{contact.name}</p>
                    <StatusBadge status={formatControlledValue(contact.contact_type)} />
                    {contact.is_primary ? <StatusBadge status="Active" /> : null}
                  </div>
                  <p className="mt-1 text-sm text-slate-600">{[contact.company, contact.job_title].filter(Boolean).join(" - ")}</p>
                  <p className="mt-1 text-sm text-slate-600">{[contact.email, contact.phone, contact.mobile].filter(Boolean).join(" | ")}</p>
                </div>
                <button
                  type="button"
                  onClick={() => onDelete(contact.id)}
                  className="h-9 rounded-md border border-slate-300 px-3 text-sm font-semibold text-slate-700"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="text-base font-semibold text-slate-950">Add Contact</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Contact Type</span>
            <select name="contact_type" defaultValue="site_contact" className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm">
              {buildingContactTypes.map((type) => (
                <option key={type.key} value={type.key}>
                  {type.label}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Name</span>
            <input name="name" required className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Company</span>
            <input name="company" className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Job Title</span>
            <input name="job_title" className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Email</span>
            <input name="email" type="email" className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Phone</span>
            <input name="phone" className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Mobile</span>
            <input name="mobile" className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
          </label>
          <label className="flex items-center gap-2 pt-8 text-sm font-medium text-slate-700">
            <input name="is_primary" type="checkbox" className="h-4 w-4" />
            Primary
          </label>
          <label className="flex items-center gap-2 pt-8 text-sm font-medium text-slate-700">
            <input name="is_emergency_contact" type="checkbox" className="h-4 w-4" />
            Emergency Contact
          </label>
          <label className="block md:col-span-2 xl:col-span-3">
            <span className="text-sm font-medium text-slate-700">Notes</span>
            <textarea name="notes" className="mt-2 min-h-20 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
          </label>
        </div>
        <div className="mt-5 flex justify-end">
          <button type="submit" disabled={isSubmitting} className="h-11 rounded-md bg-slate-950 px-5 text-sm font-semibold text-white disabled:bg-slate-400">
            {isSubmitting ? "Saving..." : "Add Contact"}
          </button>
        </div>
      </form>
    </section>
  );
}
