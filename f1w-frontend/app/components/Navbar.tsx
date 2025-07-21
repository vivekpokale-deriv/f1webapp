"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="bg-white shadow-md mb-6">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <Link href="/" className="text-xl font-bold text-[#e10600]">
            F1 Data Visualization
          </Link>
          <div className="flex space-x-4">
            <NavLink href="/" active={pathname === "/"}>
              Home
            </NavLink>
            <NavLink href="/telemetry" active={pathname === "/telemetry"}>
              Telemetry
            </NavLink>
            <NavLink href="/race-analysis" active={pathname === "/race-analysis"}>
              Race Analysis
            </NavLink>
            <NavLink href="/information" active={pathname === "/information"}>
              Information
            </NavLink>
          </div>
        </div>
      </div>
    </nav>
  );
}

interface NavLinkProps {
  href: string;
  active: boolean;
  children: React.ReactNode;
}

function NavLink({ href, active, children }: NavLinkProps) {
  return (
    <Link
      href={href}
      className={`px-3 py-2 rounded-md text-sm font-medium ${
        active
          ? "bg-[#e10600] text-white"
          : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
      }`}
    >
      {children}
    </Link>
  );
}
