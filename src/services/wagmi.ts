/**
 * Wagmi + RainbowKit Configuration
 * ================================
 * Web3 wallet connection for EVM chains.
 */
import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import {
  mainnet,
  base,
  bsc,
} from 'wagmi/chains';
import { http } from 'wagmi';

const projectId = import.meta.env.VITE_WALLETCONNECT_PROJECT_ID || 'rmi-default-project-id';

export const config = getDefaultConfig({
  appName: 'RugMunch Intelligence',
  appDescription: 'AI-powered crypto scam detection & forensics',
  appUrl: 'https://rugmunch.io',
  appIcon: 'https://rugmunch.io/icon.png',
  projectId,
  chains: [mainnet, base, bsc],
  transports: {
    [mainnet.id]: http(),
    [base.id]: http(),
    [bsc.id]: http(),
  },
  ssr: false,
});

export { mainnet, base, bsc };
