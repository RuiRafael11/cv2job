"use client";

import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ButtonHTMLAttributes,
  type HTMLAttributes,
} from "react";
import { ChevronDown } from "lucide-react";

type AccordionContextValue = {
  value: string;
  setValue: (value: string) => void;
  collapsible: boolean;
};

type AccordionItemContextValue = {
  value: string;
  open: boolean;
};

const AccordionContext = createContext<AccordionContextValue | null>(null);
const AccordionItemContext = createContext<AccordionItemContextValue | null>(null);

type AccordionProps = HTMLAttributes<HTMLDivElement> & {
  type?: "single";
  collapsible?: boolean;
  defaultValue?: string;
};

export function Accordion({
  collapsible = false,
  defaultValue = "",
  className = "",
  children,
  ...props
}: AccordionProps) {
  const [value, setInternalValue] = useState(defaultValue);
  const context = useMemo<AccordionContextValue>(
    () => ({
      value,
      collapsible,
      setValue: (nextValue) => {
        setInternalValue((current) =>
          collapsible && current === nextValue ? "" : nextValue,
        );
      },
    }),
    [collapsible, value],
  );

  return (
    <AccordionContext.Provider value={context}>
      <div className={className} {...props}>
        {children}
      </div>
    </AccordionContext.Provider>
  );
}

type AccordionItemProps = HTMLAttributes<HTMLDivElement> & {
  value: string;
};

export function AccordionItem({
  value,
  className = "",
  children,
  ...props
}: AccordionItemProps) {
  const accordion = useAccordion();
  const open = accordion.value === value;

  return (
    <AccordionItemContext.Provider value={{ value, open }}>
      <div className={className} data-state={open ? "open" : "closed"} {...props}>
        {children}
      </div>
    </AccordionItemContext.Provider>
  );
}

export function AccordionTrigger({
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  const accordion = useAccordion();
  const item = useAccordionItem();

  return (
    <button
      type="button"
      aria-expanded={item.open}
      className={`flex w-full items-center justify-between gap-4 ${className}`}
      onClick={() => accordion.setValue(item.value)}
      {...props}
    >
      <span>{children}</span>
      <ChevronDown
        className={`h-4 w-4 shrink-0 text-oxblood transition-transform ${
          item.open ? "rotate-180" : ""
        }`}
      />
    </button>
  );
}

export function AccordionContent({
  className = "",
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  const item = useAccordionItem();

  if (!item.open) {
    return null;
  }

  return (
    <div className={className} data-state="open" {...props}>
      {children}
    </div>
  );
}

function useAccordion() {
  const context = useContext(AccordionContext);
  if (!context) {
    throw new Error("Accordion components must be used inside Accordion.");
  }
  return context;
}

function useAccordionItem() {
  const context = useContext(AccordionItemContext);
  if (!context) {
    throw new Error("Accordion trigger/content must be used inside AccordionItem.");
  }
  return context;
}
