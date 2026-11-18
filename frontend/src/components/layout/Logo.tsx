import Image from "next/image";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface LogoProps {
  tone?: "default" | "light";
  className?: string;
}

/** Logotipo oficial fornecido no manual de marca do SAFEpass. */
export function Logo({ tone = "default", className }: LogoProps) {
  const src = tone === "light" ? "/brand/safepass-logo-footer.png" : "/brand/safepass-logo.png";

  return (
    <Link href="/" aria-label="SAFEpass — página inicial" className={cn("inline-flex shrink-0 items-center", className)}>
      <Image
        src={src}
        alt="SAFEpass"
        width={184}
        height={47}
        priority
        className="h-8 w-auto object-contain sm:h-10"
      />
    </Link>
  );
}
