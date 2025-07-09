import { ToggleMode } from "./toggle-mode";
import { ModelSelect } from "./model-select";
import { ReactNode } from "react";

interface HeaderProps {
  children?: ReactNode;
}

/**
 * Header Component
 * Fixed header displaying the app name with a blur effect background
 */
export const Header = ({ children }: HeaderProps) => (
  <header className="sticky top-0 z-50">
    <div className="max-w-3xl mx-auto flex flex-col gap-2 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold bg-background shadow-md p-2 rounded-full">
          Nutrix AI
        </h1>
        <div className="flex items-center gap-2">
          {children}
          <ToggleMode />
        </div>
      </div>
    </div>
  </header>
);
