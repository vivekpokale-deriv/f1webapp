import { ReactNode } from "react";
import Link from "next/link";

interface ButtonProps {
  children: ReactNode;
  href?: string;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "outline";
  className?: string;
  type?: "button" | "submit" | "reset";
}

export default function Button({
  children,
  href,
  onClick,
  variant = "primary",
  className = "",
  type = "button",
}: ButtonProps) {
  const baseClasses = "inline-flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors";
  
  const variantClasses = {
    primary: "f1-button",
    secondary: "bg-[#15151e] hover:bg-[#2a2a3c] border-transparent text-white focus:ring-[#15151e]",
    outline: "bg-transparent hover:bg-[#1e1e2a] border border-[#e10600] text-white focus:ring-[#e10600]",
  };
  
  const buttonClasses = `${baseClasses} ${variantClasses[variant]} ${className}`;
  
  if (href) {
    return (
      <Link href={href} className={buttonClasses}>
        {children}
      </Link>
    );
  }
  
  return (
    <button type={type} onClick={onClick} className={buttonClasses}>
      {children}
    </button>
  );
}
