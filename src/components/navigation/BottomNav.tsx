import { NavLink } from "react-router-dom";

const tabs = [
  { to: "/", label: "Home" },
  { to: "/learn", label: "Learn" },
  { to: "/practice", label: "Practice" },
  { to: "/progress", label: "Progress" },
] as const;

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 inset-x-0 border-t border-stone-200 bg-white/95 backdrop-blur pb-[env(safe-area-inset-bottom)]">
      <ul className="mx-auto grid max-w-3xl grid-cols-4 gap-1 px-2 py-2">
        {tabs.map((tab) => (
          <li key={tab.to}>
            <NavLink
              to={tab.to}
              className={({ isActive }) =>
                [
                  "flex min-h-12 items-center justify-center rounded-xl text-sm font-medium",
                  isActive
                    ? "bg-amber-100 text-amber-900"
                    : "text-stone-600 hover:bg-stone-100",
                ].join(" ")
              }
              end={tab.to === "/"}
            >
              {tab.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}