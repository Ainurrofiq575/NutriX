import { ToggleMode } from "./toggle-mode";

/**
 * Header Component
 * Fixed header displaying the app name with a blur effect background
 */
export const Header = () => (
  <header className="sticky top-0 z-50">
    <div className="max-w-3xl mx-auto flex items-center justify-between p-4">
      <h1 className="text-xl font-semibold bg-background shadow-md p-2 ">
        Nutrix AI
      </h1>
      <ToggleMode/>
    </div>
  </header>
);
