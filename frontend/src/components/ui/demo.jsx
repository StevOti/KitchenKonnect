import React, { useState } from "react"
import { Link } from 'react-router-dom'
import { HoveredLink, Menu, MenuItem, ProductItem } from "./navbar-menu"
import { cn } from "../../lib/utils"

export function NavbarDemo() {
  return (
    <div className="relative w-full">
      <Navbar className="top-2" />
      {/* Spacer to account for fixed navbar height so content isn't overlapped */}
      <div className="pt-28 flex items-center justify-center">
        <p className="text-black">The Navbar will show on top of the page</p>
      </div>
    </div>
  )
}

function Navbar({ className }) {
  const [active, setActive] = useState(null)
  return (
    <div className={cn("fixed top-10 inset-x-0 max-w-4xl mx-auto z-50 px-4", className)}>
      <div className="flex items-center justify-between">
        <div className="flex-1 relative">
          {/* Center the Menu at the bottom border of the navbar */}
          <div className="absolute left-1/2 bottom-0 transform translate-y-1/2 -translate-x-1/2">
            <Menu setActive={setActive}>
        <MenuItem setActive={setActive} active={active} item="Services">
          <div className="flex flex-col space-y-4 text-sm">
            <HoveredLink to="/web-dev">Web Development</HoveredLink>
            <HoveredLink to="/interface-design">Interface Design</HoveredLink>
            <HoveredLink to="/seo">Search Engine Optimization</HoveredLink>
            <HoveredLink to="/branding">Branding</HoveredLink>
          </div>
        </MenuItem>
        <MenuItem setActive={setActive} active={active} item="Products">
          <div className="text-sm grid grid-cols-2 gap-10 p-4">
            <ProductItem
              title="Algochurn"
              href="https://algochurn.com"
              src="https://images.unsplash.com/photo-1545235617-9465c3d3a0a6?w=800"
              description="Prepare for tech interviews like never before."
            />
            <ProductItem
              title="Tailwind Master Kit"
              href="https://tailwindmasterkit.com"
              src="https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?w=800"
              description="Production ready Tailwind css components for your next project"
            />
            <ProductItem
              title="Moonbeam"
              href="https://gomoonbeam.com"
              src="https://images.unsplash.com/photo-1509395176047-4a66953fd231?w=800"
              description="Never write from scratch again. Go from idea to blog in minutes."
            />
            <ProductItem
              title="Rogue"
              href="https://userogue.com"
              src="https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d?w=800"
              description="Respond to government RFPs, RFIs and RFQs 10x faster using AI"
            />
          </div>
        </MenuItem>
        <MenuItem setActive={setActive} active={active} item="Pricing">
          <div className="flex flex-col space-y-4 text-sm">
            <HoveredLink to="/hobby">Hobby</HoveredLink>
            <HoveredLink to="/individual">Individual</HoveredLink>
            <HoveredLink to="/team">Team</HoveredLink>
            <HoveredLink to="/enterprise">Enterprise</HoveredLink>
          </div>
        </MenuItem>
            </Menu>
          </div>
        </div>
        <div className="hidden sm:flex space-x-4 ml-6">
          <Link to="/home" className="text-sm text-neutral-800 hover:text-black">Home</Link>
          <Link to="/public" className="text-sm text-neutral-800 hover:text-black">Public</Link>
          <Link to="/admin/users" className="text-sm text-neutral-800 hover:text-black">Manage Users</Link>
          <Link to="/admin/verifications" className="text-sm text-neutral-800 hover:text-black">Verifications</Link>
          <Link to="/admin-only" className="text-sm text-neutral-800 hover:text-black">Admin Page</Link>
          <Link to="/nutritionist-only" className="text-sm text-neutral-800 hover:text-black">Nutritionist Page</Link>
          <Link to="/regulator-only" className="text-sm text-neutral-800 hover:text-black">Regulator Page</Link>
        </div>
      </div>
    </div>
  )
}
