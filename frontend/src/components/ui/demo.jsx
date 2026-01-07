import React, { useState } from "react";
import { HoveredLink, Menu, MenuItem, ProductItem } from "./navbar-menu";

export function NavbarDemo() {
  return (
    <div className="relative w-full flex items-center justify-center">
      <Navbar className="top-2" />
      <p className="text-black">The Navbar will show on top of the page</p>
    </div>
  );
}

function Navbar({ className }) {
  const [active, setActive] = useState(null);
  return (
    <div className={"fixed top-10 inset-x-0 max-w-2xl mx-auto z-50 " + (className || "") }>
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
              src="https://images.unsplash.com/photo-1522204509399-0cf3de70c4f1"
              description="Prepare for tech interviews like never before."
            />
            <ProductItem
              title="Tailwind Master Kit"
              href="https://tailwindmasterkit.com"
              src="https://images.unsplash.com/photo-1504674900247-0877df9cc836"
              description="Production ready Tailwind css components for your next project"
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
  );
}
