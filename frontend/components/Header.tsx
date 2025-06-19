import { ToggleMode } from "./toggle-mode";
import { ModelSelect } from "./model-select";

interface HeaderProps {
  selectedModel: "gemini" | "nutrix";
  onModelChange: (model: "gemini" | "nutrix") => void;
}

/**
 * Header Component
 * Fixed header displaying the app name with a blur effect background
 */
export const Header = ({ selectedModel, onModelChange }: HeaderProps) => (
  <header className="sticky top-0 z-50">
    <div className="max-w-3xl mx-auto flex flex-col gap-2 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold bg-background shadow-md p-2 rounded-full">
          Nutrix AI
        </h1>
        <div className="flex items-center gap-2">
          <ModelSelect
            selectedModel={selectedModel}
            onModelChange={onModelChange}
          />
          <ToggleMode />
        </div>
      </div>
    </div>
  </header>
);
