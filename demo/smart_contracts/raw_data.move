/// Module: raw_data
///
/// Stores raw data from data pipelines (NOT agents) on SUI blockchain.
///
/// This module handles storage of unprocessed data fetched by pipelines:
/// - News articles from NewsPipeline
/// - Price data from PricePipeline
///
/// Key Distinction:
/// - producer_type = "pipeline" (NOT "agent")
/// - No reasoning traces (just raw data)
/// - Used by agents as input for LLM processing
module glass_box::raw_data {
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use sui::event;

    /// Struct to store raw data from pipelines on-chain
    struct RawDataObject has key, store {
        id: UID,
        /// Producer identifier (e.g., "news_pipeline", "price_pipeline")
        producer: vector<u8>,
        /// Type of producer - always "pipeline" for non-agent processors
        producer_type: vector<u8>,
        /// Type of data (e.g., "news_raw", "price_raw", "price_historical")
        data_type: vector<u8>,
        /// Timestamp when data was published (Unix epoch)
        timestamp: u64,
        /// JSON-serialized data payload
        data_payload: vector<u8>,
        /// SHA-256 hash of data_payload for integrity verification
        data_hash: vector<u8>,
    }

    /// Event emitted when raw data is published
    struct RawDataPublished has copy, drop {
        object_id: address,
        producer: vector<u8>,
        data_type: vector<u8>,
        timestamp: u64,
        data_hash: vector<u8>,
    }

    /// Event emitted to trigger agents (lightweight)
    struct DataAvailableEvent has copy, drop {
        event_type: vector<u8>,  // "news_available", "price_updated"
        object_id: address,      // Reference to RawDataObject
        metadata: vector<u8>,    // Small metadata for filtering (JSON)
        timestamp: u64,
    }

    /// Publish raw data to blockchain (called by pipelines)
    public entry fun publish_data(
        producer: vector<u8>,
        producer_type: vector<u8>,
        data_type: vector<u8>,
        timestamp: u64,
        data_payload: vector<u8>,
        data_hash: vector<u8>,
        ctx: &mut TxContext
    ) {
        let raw_data = RawDataObject {
            id: object::new(ctx),
            producer,
            producer_type,
            data_type,
            timestamp,
            data_payload,
            data_hash,
        };

        let object_id = object::uid_to_address(&raw_data.id);

        // Emit event for indexing
        event::emit(RawDataPublished {
            object_id,
            producer: raw_data.producer,
            data_type: raw_data.data_type,
            timestamp: raw_data.timestamp,
            data_hash: raw_data.data_hash,
        });

        // Transfer to sender (pipeline operator)
        transfer::public_transfer(raw_data, tx_context::sender(ctx));
    }

    /// Emit lightweight event to trigger agents
    public entry fun emit_data_event(
        event_type: vector<u8>,
        object_id: address,
        metadata: vector<u8>,
        timestamp: u64,
        _ctx: &mut TxContext
    ) {
        event::emit(DataAvailableEvent {
            event_type,
            object_id,
            metadata,
            timestamp,
        });
    }

    /// Make raw data object publicly shareable (for agent access)
    public entry fun share_data(raw_data: RawDataObject) {
        transfer::public_share_object(raw_data);
    }

    // === Getter functions for agents to read data ===

    /// Get producer name
    public fun get_producer(raw_data: &RawDataObject): &vector<u8> {
        &raw_data.producer
    }

    /// Get producer type (should be "pipeline")
    public fun get_producer_type(raw_data: &RawDataObject): &vector<u8> {
        &raw_data.producer_type
    }

    /// Get data type
    public fun get_data_type(raw_data: &RawDataObject): &vector<u8> {
        &raw_data.data_type
    }

    /// Get timestamp
    public fun get_timestamp(raw_data: &RawDataObject): u64 {
        raw_data.timestamp
    }

    /// Get data payload (JSON blob)
    public fun get_data_payload(raw_data: &RawDataObject): &vector<u8> {
        &raw_data.data_payload
    }

    /// Get data hash (for integrity verification)
    public fun get_data_hash(raw_data: &RawDataObject): &vector<u8> {
        &raw_data.data_hash
    }
}
