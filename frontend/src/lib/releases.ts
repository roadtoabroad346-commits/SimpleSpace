export interface ReleaseConfig {
  id: string
  label: string
  doi: string
  starts: string
  ends: string | null
  enabled: boolean
}

export const RELEASES: ReleaseConfig[] = [
  { id: 'dr1', label: 'Data Release 1', doi: '10.26131/IRSA678', starts: '2025-05-01', ends: null, enabled: true },
  { id: 'qr3', label: 'Quick Release 3', doi: '10.26131/IRSA662', starts: '2026-05-16', ends: null, enabled: true },
  { id: 'dr1-cube', label: 'DR1 All-Sky Cube', doi: '10.26131/IRSA679', starts: '2025-05-01', ends: null, enabled: false },
]

export function releaseForDoi(doi: string): ReleaseConfig | undefined {
  return RELEASES.find(release => release.doi === doi)
}

export function enabledReleases(): ReleaseConfig[] {
  return RELEASES.filter(release => release.enabled)
}
