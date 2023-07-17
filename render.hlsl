Texture2D<uint> world : register(t0);
Texture1D<float4> colours : register(t1);
RWTexture2D<float4> target : register(u0);

[numthreads(8,8,1)]
void main(int3 global_pos : SV_DispatchThreadID)
{
    int2 pos = global_pos.xy;
     int2 scaled_pos = pos / 10;
    target[pos] = colours[world[scaled_pos]];
}
