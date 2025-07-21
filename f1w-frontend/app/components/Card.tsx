import { ReactNode } from "react";

interface CardProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export default function Card({ title, children, className = "" }: CardProps) {
  return (
    <div className={`f1-card card-hover ${className}`}>
      <div className="f1-card-header">
        {title}
      </div>
      <div className="f1-card-body">
        {children}
      </div>
    </div>
  );
}
