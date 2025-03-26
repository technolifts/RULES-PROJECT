export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-6">Welcome to DocSecure</h1>
      <p className="text-xl mb-8">A secure document management system</p>
      <div className="flex gap-4">
        <a 
          href="/login" 
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Login
        </a>
        <a 
          href="/register" 
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Register
        </a>
      </div>
    </div>
  )
}
