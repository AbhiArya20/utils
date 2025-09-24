const { execSync } = require('child_process');
const path = require('path');

// Run shell commands
function run(cmd, options = {}) {
  return execSync(cmd, { encoding: 'utf8', stdio: 'pipe', ...options }).trim();
}

// Generate a random time (0–23h, 0–59m, 0–59s)
function randomTime() {
  const hour = Math.floor(Math.random() * 24);
  const minute = Math.floor(Math.random() * 60);
  const second = Math.floor(Math.random() * 60);
  return { hour, minute, second };
}

// Check if a string is PascalCase
function isPascalCase(name) {
  return /^[A-Z][a-zA-Z0-9]*$/.test(name);
}

// Convert PascalCase to "natural language"
function pascalToNatural(str) {
  return str
    .replace(/([A-Z])/g, ' $1')       // insert space before capital letters
    .replace(/^ /, '')                // remove leading space
    .toLowerCase();                   // lowercase the whole thing
}

function main() {
  try {
    // 1. Get last commit date
    const lastDateStr = run('git log -1 --format=%cd --date=iso');
    const lastDate = new Date(lastDateStr);
    if (isNaN(lastDate)) throw new Error('Could not parse last commit date');

    // 2. Add 1 day and randomize time
    const nextDate = new Date(lastDate);
    nextDate.setDate(nextDate.getDate() + 1);
    const { hour, minute, second } = randomTime();
    nextDate.setHours(hour, minute, second, 0);
    const isoNextDate = nextDate.toISOString();

    console.log(lastDateStr);
    console.log(isoNextDate);
    
    
    // 3. Get staged files
    const stagedFiles = run('git diff --cached --name-only')
      .split('\n')
      .filter(Boolean);

    if (stagedFiles.length === 0) {
      console.log('❌ No files staged for commit.');
      process.exit(0);
    }

    // 4. Filter PascalCase base names and convert to natural language
    const naturalNames = stagedFiles
      .map(file => path.basename(file, path.extname(file))) // Get base name (no path, no extension)
      .map(name => name.slice(3)) // Remove non-alphanumeric characters
      .filter(isPascalCase)
      .map(pascalToNatural);

    if (naturalNames.length === 0) {
      console.log('❌ No PascalCase files found. Aborting.');
      process.exit(1);
    }

    // 5. Create commit message
    const commitMessage = `${naturalNames.join(' and ')}`;

    // 6. Commit with date flags
    const commitCmd = `git commit --date="${isoNextDate}" -m "${commitMessage}"`;
    console.log(`📅 Committing with date: ${isoNextDate}`);
    console.log(`📝 Commit message: ${commitMessage}`);
    run(commitCmd, {
      env: {
        ...process.env,
        GIT_COMMITTER_DATE: isoNextDate,
      },
    });

    // 7. Push
    console.log('🚀 Pushing...');
    // run('git push');

    console.log('✅ Commit and push completed.');
  } catch (err) {
    console.error('❌ Error:', err.message);
    process.exit(1);
  }
}

setInterval(main, 10000);