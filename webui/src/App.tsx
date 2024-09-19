import "./App.css";

import { createBrowserRouter, RouterProvider } from "react-router-dom";
import ChartPage from "./pages/ChartPage";
import { EditorLayout } from "./pages/EditorLayout";
import LogPage from "./pages/LogPage";
import { PrepareSimaple } from "./pages/PrepareSimaple";

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
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
