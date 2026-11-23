import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import { ConnectionBanner, UpdatePrompt, WakingOverlay } from "./components/Overlays";
import { Toasts } from "./components/ui";
import { CreateScreen } from "./screens/Create";
import { Home } from "./screens/Home";
import { RoomScreen } from "./screens/Room";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/crear" element={<CreateScreen />} />
        <Route path="/r/:code" element={<RoomScreen />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <WakingOverlay />
      <ConnectionBanner />
      <UpdatePrompt />
      <Toasts />
    </BrowserRouter>
  );
}
