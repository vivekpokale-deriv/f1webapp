interface PageHeaderProps {
  title: string;
  description?: string;
}

export default function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="bg-[#e10600] text-white py-8 mb-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold">{title}</h1>
        {description && <p className="mt-2 text-lg opacity-90">{description}</p>}
      </div>
    </div>
  );
}
