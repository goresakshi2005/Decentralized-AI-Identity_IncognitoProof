const hre = require("hardhat");

async function main() {
  const CredentialRegistry = await hre.ethers.getContractFactory("CredentialRegistry");
  const credentialRegistry = await CredentialRegistry.deploy();
  await credentialRegistry.waitForDeployment();
  
  const RevocationRegistry = await hre.ethers.getContractFactory("RevocationRegistry");
  const revocationRegistry = await RevocationRegistry.deploy();
  await revocationRegistry.waitForDeployment();
  
  const IssuerRegistry = await hre.ethers.getContractFactory("IssuerRegistry");
  const issuerRegistry = await IssuerRegistry.deploy();
  await issuerRegistry.waitForDeployment();
  
  console.log("CredentialRegistry deployed to:", await credentialRegistry.getAddress());
  console.log("RevocationRegistry deployed to:", await revocationRegistry.getAddress());
  console.log("IssuerRegistry deployed to:", await issuerRegistry.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});