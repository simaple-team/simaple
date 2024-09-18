import "./App.css";

import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { PrepareSimaple } from "./pages/PrepareSimaple";
import { EditorLayout } from "./pages/EditorLayout";
import ChartPage from "./pages/ChartPage";

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
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
