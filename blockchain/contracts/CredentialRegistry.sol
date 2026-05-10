// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract CredentialRegistry {
    struct CredentialAnchor {
        string credentialId;
        string signatureHash;
        uint256 timestamp;
        address issuer;
        bool active;
    }
    
    mapping(string => CredentialAnchor) public credentials;
    mapping(address => bool) public authorizedIssuers;
    address public admin;
    
    event CredentialAnchored(string indexed credentialId, address issuer, uint256 timestamp);
    event CredentialRevoked(string indexed credentialId, address revoker);
    event IssuerAuthorized(address indexed issuer);
    event IssuerRevoked(address indexed issuer);
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }
    
    modifier onlyAuthorizedIssuer() {
        require(authorizedIssuers[msg.sender], "Not authorized issuer");
        _;
    }
    
    constructor() {
        admin = msg.sender;
    }
    
    function authorizeIssuer(address issuer) external onlyAdmin {
        authorizedIssuers[issuer] = true;
        emit IssuerAuthorized(issuer);
    }
    
    function revokeIssuer(address issuer) external onlyAdmin {
        authorizedIssuers[issuer] = false;
        emit IssuerRevoked(issuer);
    }
    
    function anchorCredential(
        string memory credentialId,
        string memory signatureHash
    ) external onlyAuthorizedIssuer {
        require(bytes(credentials[credentialId].credentialId).length == 0, "Credential already anchored");
        
        credentials[credentialId] = CredentialAnchor({
            credentialId: credentialId,
            signatureHash: signatureHash,
            timestamp: block.timestamp,
            issuer: msg.sender,
            active: true
        });
        
        emit CredentialAnchored(credentialId, msg.sender, block.timestamp);
    }
    
    function revokeCredential(string memory credentialId) external {
        require(
            msg.sender == credentials[credentialId].issuer || msg.sender == admin,
            "Not authorized to revoke"
        );
        require(credentials[credentialId].active, "Credential not active");
        
        credentials[credentialId].active = false;
        emit CredentialRevoked(credentialId, msg.sender);
    }
    
    function verifyCredential(string memory credentialId) external view returns (bool active, address issuer) {
        CredentialAnchor memory cred = credentials[credentialId];
        return (cred.active, cred.issuer);
    }
}