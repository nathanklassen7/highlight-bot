import { Link } from "react-router-dom";

const links = [
  { to: "/clips", label: "View Clips" },
  { to: "/config", label: "Camera" },
  { to: "/wifi", label: "WiFi Settings" },
];

export function NavLinks() {
  return (
    <div className="space-y-3">
      {links.map((link) => (
        <Link
          key={link.to}
          to={link.to}
          className="block p-4 bg-white rounded-lg shadow-sm hover:bg-gray-50 text-center font-medium text-gray-900"
        >
          {link.label}
        </Link>
      ))}
    </div>
  );
}
