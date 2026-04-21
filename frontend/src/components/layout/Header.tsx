import { Link } from "react-router-dom";
import { useTemperature } from "../../hooks/useTemperature";

interface HeaderProps {
  title: string;
  backTo?: { label: string; path: string };
  maxWidth?: string;
}

export function Header({
  title,
  backTo,
  maxWidth = "max-w-xl",
}: HeaderProps) {
  const temp = useTemperature();

  return (
    <header className="bg-white shadow-sm">
      <div
        className={`${maxWidth} mx-auto py-4 px-4 flex justify-between items-center`}
      >
        {backTo ? (
          <Link
            to={backTo.path}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            &larr; {backTo.label}
          </Link>
        ) : (
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
        )}
        {!backTo && (
          <span className="text-sm text-gray-500">
            {temp !== null ? `${temp.toFixed(1)}°C` : ""}
          </span>
        )}
        {backTo && (
          <>
            <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
            <span className="text-sm text-gray-500">
              {temp !== null ? `${temp.toFixed(1)}°C` : ""}
            </span>
          </>
        )}
      </div>
    </header>
  );
}
