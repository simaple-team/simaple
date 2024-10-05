import { pySimaple as dev } from "./dev";
import { pySimaple as production } from "./production";

const pySimaple = import.meta.env.DEV ? dev : production;

export { pySimaple };
