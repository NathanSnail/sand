Texture2D<uint> world[$WIDTH][$HEIGHT] : register(s0);
Texture1D<float4> colours[$NUM_MATS] : register(t1);
RWTexture2D<float4> target : register(u0);

[numthreads(8,8,1)]
void main(int3 global_pos : SV_DispatchThreadID)
{
    int2 pos = global_pos.xy;
    //target[pos] = colours[world[pos/10]];
    target[pos] = float4(1,1,0,1);
}