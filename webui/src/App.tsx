import "./App.css";

import { createBrowserRouter, RouterProvider } from "react-router-dom";
import ChartPage from "./pages/ChartPage/ChartPage";
import { EditorLayout } from "./pages/EditorLayout";
import LogPage from "./pages/LogPage";
import { PrepareSimaple } from "./pages/PrepareSimaple";
import { SummaryPage } from "./pages/SummaryPage";
import { PreferencePage } from "./pages/PreferencePage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <PrepareSimaple />,
  },
  {
    path: "/editor",
    element: <EditorLayout />,
    children: [
      {
        path: "chart",
        element: <ChartPage />,
      },
      {
        path: "log",
        element: <LogPage />,
      },
      {
        path: "summary",
        element: <SummaryPage />,
      },
      {
        path: "preference",
        element: <PreferencePage />,
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
