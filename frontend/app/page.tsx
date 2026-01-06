'use client'

/**
 * Landing Page - Premium Midnight Genesis
 *
 * Premium SaaS homepage with Hebbia/OneText-inspired design
 * Bento grid layout, advanced motion orchestration, and visual depth
 */

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { motion, useReducedMotion, useScroll, useTransform, Variants } from 'framer-motion'
import { useSession } from '@/lib/auth-client'
import { useEffect, useState, useRef } from 'react'
import Footer from '@/components/Footer'

// Advanced motion variants with staggered orchestration
const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2,
    },
  },
}

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 30, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: 'spring',
      stiffness: 100,
      damping: 15,
      mass: 0.8,
    },
  },
}

const heroVariants: Variants = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 80,
      damping: 20,
      mass: 1,
    },
  },
}

export default function Home() {
  const shouldReduceMotion = useReducedMotion()
  const router = useRouter()
  const { data: session, isPending } = useSession()
  const featuresRef = useRef<HTMLDivElement>(null)

  // Scroll-based animations for features section
  const { scrollYProgress } = useScroll({
    target: featuresRef,
    offset: ['start end', 'end start'],
  })

  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0.3])

  const [hasMounted, setHasMounted] = useState(false)

  useEffect(() => {
    setHasMounted(true)
  }, [])

  useEffect(() => {
    if (hasMounted && !isPending && session?.user) {
      router.push('/dashboard')
    }
  }, [hasMounted, session, isPending, router])

  if (!hasMounted) {
    return null
  }

  if (isPending || session?.user) {
    return null
  }

  const variants = shouldReduceMotion ? {} : { containerVariants, itemVariants, heroVariants }

  return (
    <div className="min-h-screen flex flex-col bg-midnight-bg">
      <main className="flex-1 relative overflow-hidden">
        {/* Multi-layered radial gradient background */}
        <div className="absolute inset-0 bg-gradient-radial from-primary-violet/10 via-midnight-bg to-midnight-bg pointer-events-none" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-secondary-indigo/5 rounded-full blur-3xl pointer-events-none" />

        {/* Hero Section - Increased spacing */}
        <section className="relative z-10 px-4 sm:px-6 lg:px-8 pt-32 pb-24">
          <motion.div
            className="w-full max-w-4xl mx-auto text-center space-y-8"
            initial="hidden"
            animate="visible"
            variants={variants.containerVariants}
          >
            <motion.h1
              className="text-5xl sm:text-6xl md:text-7xl font-bold text-text-primary leading-tight"
              variants={variants.heroVariants}
            >
              Transform Your
              <span className="block bg-gradient-to-r from-primary-violet via-secondary-indigo to-primary-violet bg-clip-text text-transparent animate-gradient">
                Workflow Today
              </span>
            </motion.h1>

            <motion.p
              className="text-xl sm:text-2xl max-w-2xl mx-auto text-text-secondary leading-relaxed"
              variants={variants.itemVariants}
            >
              Experience premium task management with our elegant, secure platform designed for modern professionals
            </motion.p>

            <motion.div
              className="flex justify-center pt-8"
              variants={variants.itemVariants}
            >
              <Link
                href="/signup"
                className="group relative px-8 py-4 text-lg font-semibold rounded-xl transition-all duration-300 bg-gradient-to-r from-primary-violet to-secondary-indigo text-text-primary shadow-2xl shadow-primary-violet/30 hover:shadow-[0_0_40px_rgba(139,92,246,0.8)] hover:scale-105"
              >
                <span className="relative z-10">Get Started</span>
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-secondary-indigo to-primary-violet opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </Link>
            </motion.div>
          </motion.div>
        </section>

        {/* Features Section - Premium Bento Grid with increased spacing */}
        <section ref={featuresRef} className="relative z-10 px-4 sm:px-6 lg:px-8 py-32">
          <motion.div
            className="w-full max-w-7xl mx-auto"
            style={shouldReduceMotion ? {} : { opacity }}
          >
            {/* Bento Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-6 gap-6 auto-rows-fr">
              {/* Large Feature Card - Double Width */}
              <motion.div
                className="md:col-span-4 glass-card p-8 hover:bg-white/[0.15] transition-all duration-500 cursor-pointer group relative overflow-hidden"
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true, margin: '-100px' }}
                transition={{ type: 'spring', stiffness: 100, damping: 15, delay: 0.1 }}
                whileHover={{ y: -8, scale: 1.02 }}
              >
                <div className="absolute top-0 right-0 w-64 h-64 bg-primary-violet/10 rounded-full blur-3xl group-hover:bg-primary-violet/40 transition-all duration-500" />
                <div className="relative z-10">
                  <h3 className="text-2xl md:text-3xl font-bold mb-4 text-text-primary group-hover:text-primary-violet transition-colors">
                    Enterprise-Grade Security
                  </h3>
                  <p className="text-lg text-text-secondary leading-relaxed ">
                    Your tasks are protected with zero-trust architecture, end-to-end encryption, and complete data isolation. Built for teams that demand the highest security standards.
                  </p>
                  <div className="mt-6 flex items-center space-x-2 text-primary-violet">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm font-medium">SOC 2 Compliant</span>
                  </div>
                </div>
              </motion.div>

              {/* Medium Feature Card */}
              <motion.div
                className="md:col-span-2 glass-card p-6 hover:bg-white/[0.15] transition-all duration-500 cursor-pointer group"
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true, margin: '-100px' }}
                transition={{ type: 'spring', stiffness: 100, damping: 15, delay: 0.2 }}
                whileHover={{ y: -8, scale: 1.05 }}
              >
                <h3 className="text-xl font-semibold mb-3  text-text-primary group-hover:text-secondary-indigo transition-colors">
                  Beautiful Design
                </h3>
                <p className="text-base text-text-secondary">
                  Premium midnight theme with smooth 60 FPS animations and glassmorphic effects
                </p>
              </motion.div>

              {/* Small Feature Card */}
              <motion.div
                className="md:col-span-2 glass-card p-6 hover:bg-white/[0.15] transition-all duration-500 cursor-pointer group"
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true, margin: '-100px' }}
                transition={{ type: 'spring', stiffness: 100, damping: 15, delay: 0.3 }}
                whileHover={{ y: -8, scale: 1.05 }}
              >
                <h3 className="text-xl font-semibold mb-3 text-text-primary group-hover:text-primary-violet transition-colors">
                  Lightning Fast
                </h3>
                <p className="text-base text-text-secondary">
                  Built on Next.js 15 with edge runtime for instant page loads
                </p>
              </motion.div>

              {/* Medium Feature Card */}
              <motion.div
                className="md:col-span-4 glass-card p-6 hover:bg-white/[0.15] transition-all duration-500 cursor-pointer group"
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true, margin: '-100px' }}
                transition={{ type: 'spring', stiffness: 100, damping: 15, delay: 0.4 }}
                whileHover={{ y: -8, scale: 1.05 }}
              >
                <h3 className="text-xl font-semibold mb-3 text-text-primary group-hover:text-secondary-indigo transition-colors">
                  Seamless Collaboration
                </h3>
                <p className="text-base text-text-secondary">
                  Real-time sync across all your devices with intelligent conflict resolution and offline support
                </p>
              </motion.div>
            </div>
          </motion.div>
        </section>

        {/* Soft Transition to Footer - Radial Gradient Fade */}
        <div className="relative z-0 h-32 bg-gradient-to-b from-midnight-bg via-midnight-bg/50 to-transparent pointer-events-none" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      </main>
      <Footer />
    </div>
  )
}
