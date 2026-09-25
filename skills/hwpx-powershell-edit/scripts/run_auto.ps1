# run_auto.ps1 - run a Hangul COM worker script in a child process while auto-dismissing
# Hangul's file-access security prompt (MessageBoxImpl) with "allow all" (Alt+N). ASCII only.
# Never touches an Hwp process that already existed before start.
param(
    [Parameter(Mandatory = $true)][string]$Script,
    [Parameter(Mandatory = $true)][string]$HwpxPath
)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName UIAutomationClient; Add-Type -AssemblyName UIAutomationTypes; Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System; using System.Runtime.InteropServices;
public class FG2 { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); }
'@
$preExisting = @(Get-Process Hwp -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
if ($preExisting.Count -gt 0) { Write-Output ("note: user Hangul already running (pid " + ($preExisting -join ',') + ") - will not touch it") }
$a = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Script, '-HwpxPath', $HwpxPath)
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = 'powershell.exe'
$psi.Arguments = ($a | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }) -join ' '
$psi.RedirectStandardOutput = $true; $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
$psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
$proc = [System.Diagnostics.Process]::Start($psi)
$deadline = (Get-Date).AddSeconds(240)
while (-not $proc.HasExited -and (Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 800
    $hw = Get-Process Hwp -ErrorAction SilentlyContinue | Where-Object { $preExisting -notcontains $_.Id }
    if (-not $hw) { continue }
    foreach ($h in $hw) {
        try {
            $root = [System.Windows.Automation.AutomationElement]::RootElement
            $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $h.Id)
            $wins = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
            foreach ($w in $wins) {
                if ($w.Current.ClassName -eq 'MessageBoxImpl') {
                    [FG2]::SetForegroundWindow([IntPtr]$w.Current.NativeWindowHandle) | Out-Null
                    Start-Sleep -Milliseconds 200
                    [System.Windows.Forms.SendKeys]::SendWait('%n')
                    Write-Output 'dismissed security prompt'
                }
            }
        } catch {}
    }
}
if (-not $proc.HasExited) {
    Write-Output 'TIMEOUT'; try { $proc.Kill() } catch {}
    Get-Process Hwp -ErrorAction SilentlyContinue | Where-Object { $preExisting -notcontains $_.Id } | Stop-Process -Force
}
Write-Output $proc.StandardOutput.ReadToEnd()
