'use client'

/**
 * Premium SaaS Footer for FlowTask
 *
 * Hebbia/OneText-inspired premium design
 * Multi-column layout with professional SaaS copy
 * Enhanced with Framer Motion animations
 *
 * Owner: @css-animation-expert
 */

import Link from 'next/link'
import { motion } from 'framer-motion'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-midnight-bg border-t border-white/10 mt-36">
      <motion.div
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Column */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold bg-gradient-to-r from-primary-violet to-secondary-indigo bg-clip-text text-transparent">
              FlowTask
            </h3>
            <p className="text-sm text-text-secondary max-w-xs">
              Premium task management designed for modern professionals. Secure, beautiful, and lightning fast.
            </p>
          </div>

          {/* Product Column */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
              Product
            </h4>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/dashboard"
                  className="text-sm text-text-secondary hover:text-primary-violet transition-colors"
                >
                  Dashboard
                </Link>
              </li>
              <li>
                <Link
                  href="/dashboard"
                  className="text-sm text-text-secondary hover:text-primary-violet transition-colors"
                >
                  Flow Assistant
                </Link>
              </li>
              <li>
                <span className="text-sm text-text-secondary/50">
                  Features
                </span>
              </li>
              <li>
                <span className="text-sm text-text-secondary/50">
                  Pricing
                </span>
              </li>
            </ul>
          </div>

          {/* Company Column */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
              Company
            </h4>
            <ul className="space-y-2">
              <li>
                <span className="text-sm text-text-secondary/50">
                  About
                </span>
              </li>
              <li>
                <span className="text-sm text-text-secondary/50">
                  Blog
                </span>
              </li>
              <li>
                <span className="text-sm text-text-secondary/50">
                  Careers
                </span>
              </li>
              <li>
                <span className="text-sm text-text-secondary/50">
                  Contact
                </span>
              </li>
            </ul>
          </div>

          {/* Legal Column */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
              Legal
            </h4>
            <ul className="space-y-2">
              <li>
                <span className="text-sm text-text-secondary/50">
                  Privacy Policy
                </span>
              </li>
              <li>
                <span className="text-sm text-text-secondary/50">
                  Terms of Service
                </span>
              </li>
              <li>
                <span className="text-sm text-text-secondary/50">
                  Security
                </span>
              </li>
              <li>
                <span className="text-sm text-text-secondary/50">
                  Compliance
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar with Social Icons */}
        <div className="mt-12 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <p className="text-sm text-text-secondary">
            © {currentYear} FlowTask. All rights reserved.
          </p>

          {/* Social Icons */}
          <div className="flex items-center space-x-6">
            {/* GitHub Icon */}
            <a
              href="#"
              className="text-text-secondary hover:text-primary-violet transition-colors"
              aria-label="GitHub"
            >
              <svg
                className="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  fillRule="evenodd"
                  clipRule="evenodd"
                  d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"
                />
              </svg>
            </a>

            {/* Twitter/X Icon */}
            <a
              href="#"
              className="text-text-secondary hover:text-primary-violet transition-colors"
              aria-label="Twitter"
            >
              <svg
                className="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </a>

            {/* LinkedIn Icon */}
            <a
              href="#"
              className="text-text-secondary hover:text-primary-violet transition-colors"
              aria-label="LinkedIn"
            >
              <svg
                className="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
              </svg>
            </a>
          </div>
        </div>
      </motion.div>
    </footer>
  )
}
