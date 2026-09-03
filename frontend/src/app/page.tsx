export default function Home() {
  return (
    <main className="flex h-screen w-full flex-col items-center justify-center bg-forest-900 p-8">
      <div className="text-center max-w-2xl">
        <h1 className="mb-4 text-4xl font-bold tracking-tight sm:text-6xl">
          VANRAKSHA AI
        </h1>
        <p className="mb-8 text-lg text-gray-300">
          Forest Command Centre — Detection, Correlation, Risk Assessment, and Incident Management
        </p>
        <div className="space-x-4">
          <a
            href="/command"
            className="inline-flex items-center justify-center rounded-md bg-forest-600 px-6 py-3 text-base font-medium text-white hover:bg-forest-500 transition-colors"
          >
            Open Command Centre
          </a>
          <a
            href="/login"
            className="inline-flex items-center justify-center rounded-md border border-gray-600 px-6 py-3 text-base font-medium text-gray-200 hover:bg-gray-800 transition-colors"
          >
            Sign In
          </a>
        </div>
        <p className="mt-8 text-sm text-gray-500">
          AI outputs require human verification.
        </p>
      </div>
    </main>
  );
}