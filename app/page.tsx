import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Music from "@/components/Music";
import Videos from "@/components/Videos";
import About from "@/components/About";
import Booking from "@/components/Booking";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Music />
        <Videos />
        <About />
        <Booking />
      </main>
      <Footer />
    </>
  );
}
