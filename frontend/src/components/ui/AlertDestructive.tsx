import { AlertCircle } from "lucide-react"

import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert"
  
export function AlertDestructive({error}: {error: string}) {
  return (
    <Alert variant="destructive" className="lg:w-[600px] w-[400px] mb-10">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>
        {error}
      </AlertDescription>
    </Alert>
  )
}