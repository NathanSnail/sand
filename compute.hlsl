cbuffer Config : register(b0)
{
    uint offset;
};

/*

config:
    offset u32 %2 == y // 2 == x

inf_array:
    density f32

inf_array:
    type u32

// col_array:
//     colour vec4<f32>

reactions:
    product arr<vec2<u32>>

world:
    mat_ids arr<u32>
*/

// 8 material types in a 65x65
Texture2DArray<uint> world[$WIDTH][$HEIGHT] : register(s0);
Texture1DArray<float> density[$NUM_MATS] : register(t0);
Texture1DArray<uint> type[$NUM_MATS] : register(t1);

[numthreads(8,8,1)]
void main(int3 global_pos : SV_DispatchThreadID)
{
    uint2 pos = global_pos.xy * 2 + offset;
}
