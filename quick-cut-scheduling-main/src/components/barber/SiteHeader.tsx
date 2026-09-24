import { useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "@tanstack/react-router";
import { LogOut, Menu } from "lucide-react";
import { useEffect, useState } from "react";

import { Logo } from "./Logo";
import { Button } from "@/components/ui/button";
import { logout, useCurrentUser } from "@/lib/barber-store";

const links = [
  { to: "/", label: "Inicio" },
  { to: "/servicios", label: "Servicios" },
  { to: "/reservar", label: "Reservar" },
] as const;

export function SiteHeader() {
  const currentUser = useCurrentUser();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  useEffect(() => setHydrated(true), []);
  const user = hydrated ? currentUser : null;


  const nav = (
    <>
      {links.map((l) => (
        <Link
          key={l.to}
          to={l.to}
          onClick={() => setOpen(false)}
          activeOptions={{ exact: l.to === "/" }}
          activeProps={{ className: "text-primary" }}
          className="text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          {l.label}
        </Link>
      ))}
      {user?.role === "cliente" && (
        <Link
          to="/mis-turnos"
          onClick={() => setOpen(false)}
          activeProps={{ className: "text-primary" }}
          className="text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          Mis turnos
        </Link>
      )}
      {user?.role === "admin" && (
        <Link
          to="/admin"
          onClick={() => setOpen(false)}
          activeProps={{ className: "text-primary" }}
          className="text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          Dashboard
        </Link>
      )}
    </>
  );

  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/85 backdrop-blur">
      <div className="mx-auto grid h-16 max-w-6xl grid-cols-[minmax(0,1fr)_auto] items-center gap-2 px-3 sm:gap-4 sm:px-4 md:grid-cols-[auto_minmax(0,1fr)_auto]">
        <Logo className="min-w-0 [&>span:last-child]:hidden min-[390px]:[&>span:last-child]:block" />
        <nav className="hidden min-w-0 items-center justify-self-end gap-7 md:flex">{nav}</nav>
        <div className="flex shrink-0 items-center gap-1 sm:gap-2">
          {user ? (
            <>
              <span className="hidden text-sm text-muted-foreground sm:inline">{user.nombre}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  logout();
                  queryClient.clear();
                  navigate({ to: "/", replace: true });
                }}
              >
                <LogOut className="size-4" /> <span className="hidden sm:inline">Salir</span>
              </Button>
            </>
          ) : (
            <Button asChild size="sm">
              <Link to="/auth">Ingresar</Link>
            </Button>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setOpen((o) => !o)}
            aria-label="Abrir menú"
          >
            <Menu className="size-5" />
          </Button>
        </div>
      </div>
      {open && <nav className="flex flex-col gap-3 border-t border-border/60 px-4 py-4 md:hidden">{nav}</nav>}
    </header>
  );
}
