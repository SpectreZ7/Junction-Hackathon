import { Link, useLocation } from "react-router-dom";
import { Home, Brain, DollarSign, Plane, Heart } from "lucide-react";

const BottomNav = () => {
  const location = useLocation();
  
  const navItems = [
    { path: "/", icon: Home, label: "Home" },
    { path: "/coach", icon: Brain, label: "AI Coach" },
    { path: "/earnings", icon: DollarSign, label: "Earnings" },
    { path: "/airport", icon: Plane, label: "Airport" },
    { path: "/wellbeing", icon: Heart, label: "Wellbeing" },
  ];

  return (
    <nav className="absolute bottom-0 left-0 right-0 bg-card border-t border-border z-50">
      <div className="flex justify-around items-center h-20 px-2">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className="flex flex-col items-center justify-center gap-1 flex-1 py-2 transition-colors"
            >
              <Icon 
                className={`w-6 h-6 transition-all ${
                  isActive 
                    ? "text-primary scale-110" 
                    : "text-muted-foreground"
                }`}
              />
              <span 
                className={`text-xs transition-colors ${
                  isActive 
                    ? "text-primary font-medium" 
                    : "text-muted-foreground"
                }`}
              >
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};

export default BottomNav;
